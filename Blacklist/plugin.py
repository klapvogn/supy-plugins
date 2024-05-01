###
# Copyright (c) 2022, Mike Oxlong
# V1.01 - Because bugs are an inevitability!
###

import json, os, time, threading

from supybot.commands import *
from supybot import callbacks, conf, ircmsgs, ircutils, schedule

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Blacklist')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

class Blacklist(callbacks.Plugin):
    """A custom ban tracking plugin to keep a channel's banlist cleaner"""
    
    banmasks = {0: '*!ident@host',
                1: '*!*ident@host',
                2: '*!*@host',
                3: '*!*ident@*.phost',
                4: '*!*@*.phost',
                5: 'nick!ident@host',
                6: 'nick!*ident@host',
                7: 'nick!*@host',
                8: 'nick!*ident@*.phost',
                9: 'nick!*@*.phost',
                10: '*!ident@*'}
    
    threaded = True
    def __init__(self, irc):
        self.__parent = super(Blacklist, self)
        self.__parent.__init__(irc)
        self.dbfile = os.path.join(str(conf.supybot.directories.data), 'Blacklist', 'blacklist.json')
        self.db = {}
        self._initdb()
    
    def _initdb(self):
        try:
            with open(self.dbfile, 'r') as f: self.db = json.load(f)
        except IOError:
            self._dbWrite()
    
    def _write(self, lock):
        if not os.path.exists(os.path.dirname(self.dbfile)):
            os.mkdir(os.path.dirname(self.dbfile))
        with lock, open(self.dbfile, 'w') as f: json.dump(self.db, f)
    
    def _dbWrite(self):
        lock = threading.Lock()
        threading.Thread(target=self._write,args=(lock,)).start()
    
    def _elapsed(self, inp):
        lapsed = int(time.time()-inp)
        L = (1, 60, 3600, 86400, 604800, 2592000, 31536000)
        T = ('s', 'm', 'h', 'd', 'w', 'mo')
        for l, t in zip(L, T):
            if lapsed < L[L.index(l)+1]:
                return f'{int(lapsed/l)}{t}'
        return f'{int(lapsed/60/60/24/365)}y'
        
    def _createMask(self, irc, target, num):
        nick, ident, host = ircutils.splitHostmask(irc.state.nickToHostmask(target))
        mask = self.banmasks[num].replace('nick', nick).replace('ident', ident).replace('host', host)
        if 'phost' in mask:
            if '.' in host:
                mask = mask.replace('phost', host.split('.')[1])
            else:
                mask = mask.split('@')[0]+f'@{host}'
        return mask
    
    def doMode(self, irc, msg):
        if msg.args[1:] and msg.args[1] == '+b' and \
          not ircutils.hostmaskPatternEqual(msg.prefix, irc.prefix) and \
          self.registryValue('addManualBans', msg.args[0]) and \
          irc.state.channels[msg.args[0]].isHalfopPlus(irc.nick) and \
          not ircutils.strEqual(msg.nick, irc.nick) and \
          (msg.args[0] not in self.db or msg.args[2] not in self.db[msg.args[0]]):
            try: self.db[msg.args[0]][msg.args[2]] = [msg.nick, time.time(), '*user-added ban']
            except KeyError: self.db[msg.args[0]] = {msg.args[2]: [msg.nick, time.time(), '*user-added ban']}
            self._dbWrite()
            irc.reply(f'"{msg.args[2]}" added to database for {msg.args[0]}.')
    
    def doJoin(self, irc, msg):
        if self.registryValue('enabled', msg.args[0]) and \
          irc.state.channels[msg.args[0]].isHalfopPlus(irc.nick) and \
          not ircutils.strEqual(msg.nick, irc.nick) and msg.args[0] in self.db:
            for mask in self.db[msg.args[0]]:
                if ircutils.hostmaskPatternEqual(mask, msg.prefix):
                    irc.queueMsg(ircmsgs.ban(msg.args[0], mask))
                    irc.queueMsg(ircmsgs.kick(msg.args[0], msg.nick, self.db[msg.args[0]][mask][2]))
                    schedule.addEvent(lambda: irc.queueMsg(ircmsgs.unban(msg.args[0], mask)),
                                      time.time()+(self.registryValue('banlistExpiry', msg.args[0])*60),
                                      f'bl_unban_{msg.args[0]}{mask}')
                    break
    
    def add(self, irc, msg, args, channel, target, reason):
        """[<channel>] <nick|mask> [<reason>]
        
        Add <nick|hostmask> to blacklist database (requires #channel,op capability)"""
        self._ban(irc, msg, args, channel, target, None, reason)
    add = wrap(add, [('checkChannelCapability', 'op'), 'channel',
                     'somethingWithoutSpaces', optional('text')])
    
    def timer(self, irc, msg, args, channel, target, timer, reason):
        """[<channel>] <nick|mask> [<expiry>] [<reason>]
        
        Add <nick|hostmask> to blacklist database, expiry is given in minutes (requires #channel,op capability)"""
        if not timer: timer = self.registryValue('banTimerExpiry', channel)
        self._ban(irc, msg, args, channel, target, timer, reason)
    timer = wrap(timer, [('checkChannelCapability', 'op'), 'channel',
                         'somethingWithoutSpaces', optional('PositiveInt'),
                         optional('text')])
    
    def _ban(self, irc, msg, args, channel, target, timer, reason):
        if not self.registryValue('enabled', channel):
            irc.error(f'Database is disabled in {channel}.')
            return
        if not irc.state.channels[channel].isHalfopPlus(irc.nick):
            irc.error(f'I have no powers in {channel}.')
            return
        if channel not in irc.state.channels:
            irc.error(f'I\'m not in {channel}.')
            return
        if ircutils.isUserHostmask(target):
            if ircutils.hostmaskPatternEqual(target, irc.prefix):
                irc.error('You want me to blacklist myself?!')
                return
            mask = target
        elif irc.isNick(target):
            if ircutils.strEqual(target, irc.nick):
                irc.error('You want me to blacklist myself?!')
                return
            if target not in irc.state.channels[channel].users:
                irc.error(f'"{target}" is not in {channel}.')
                return
            mask = self._createMask(irc, target, self.registryValue('maskNumber', channel))
        else:
            irc.error(f'Invalid nick or banmask.')
            return
        if mask in irc.state.channels[channel].bans:
            irc.error(f'"{mask}" is already in banlist for {channel}.')
            return
        if not reason:
            reason = self.registryValue('banReason', channel)
        if channel not in self.db or mask not in self.db[channel]:
            try: self.db[channel][mask] = [msg.nick, int(time.time()), reason]
            except KeyError: self.db[channel] = {mask: [msg.nick, int(time.time()), reason]}
            self._dbWrite()
            irc.reply(f'"{mask}" added to the banlist for {channel}.')
        irc.queueMsg(ircmsgs.ban(channel, mask))
        for nick in irc.state.channels[channel].users:
            if ircutils.hostmaskPatternEqual(mask, irc.state.nickToHostmask(nick)):
                irc.queueMsg(ircmsgs.kick(channel, nick, reason))
        if timer:
            def _run():
                del self.db[channel][mask]
                if len(self.db[channel]) == 0:
                    del self.db[channel]
                self._dbWrite()
            schedule.addEvent(lambda: _run(),
                              time.time()+(timer*60), f'bl_db_unban_{channel}{mask}')
        else: timer = 0
        schedule.addEvent(lambda: irc.queueMsg(ircmsgs.unban(channel, mask)),
                            time.time()+(timer*60 or self.registryValue('banlistExpiry', channel)*60),
                            f'bl_unban_{channel}{mask}')
    
    def remove(self, irc, msg, args, channel, mask):
        """[<channel>] <mask>
        
        Remove a mask from the blacklist database (requires #channel,op capability)"""
        if channel not in irc.state.channels:
            irc.error(f'I\'m not in {channel}.')
            return
        if channel not in self.db or mask not in self.db[channel]:
            irc.error(f'"{mask}" is not in my banlist for {channel}.')
            return
        try:
            schedule.removeEvent(f'bl_unban_{channel}{mask}')
            schedule.removeEvent(f'bl_db_unban_{channel}{mask}')
        except: pass
        if mask in irc.state.channels[channel].bans:
            irc.queueMsg(ircmsgs.unban(channel, mask))
        del self.db[channel][mask]
        if len(self.db[channel]) == 0:
            del self.db[channel]
        self._dbWrite()
        irc.reply(f'"{mask}" removed from the banlist in {channel}.')
    remove = wrap(remove, [('checkChannelCapability', 'op'), 'channel', 'text'])
    
    def list(self, irc, msg, args, channel):
        """[<channel>]
        
        Returns a list of banmasks stored in <channel> (requires #channel,op capability)"""
        if channel not in self.db:
            irc.reply(f'The banlist for {channel} is currently empty.')
            return
        #irc.reply(f'{len(self.db[channel])} entries in {channel}...')
        padwidth = len(max((mask for mask in self.db[channel])))
        for banmask,v in self.db[channel].items():
            elapsed = self._elapsed(v[1])
            irc.reply(f'{banmask.ljust(padwidth, " ")} - Added by {v[0]} {elapsed} ago (reason: {v[2]})')
    list = wrap(list, [('checkChannelCapability', 'op'), 'channel'])

Class = Blacklist

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
