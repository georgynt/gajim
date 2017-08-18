# Copyright (c) 2009-2010, Alexander Cherniuk (ts33kr@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This module contains examples of how to create your own commands, by
creating a new command container, bounded to a specific command host,
and definding a set of commands inside of it.

Keep in mind that this module is not being loaded from anywhere, so the
code in here will not be executed and commands defined here will not be
detected.
"""

from gajim.command_system.framework import CommandContainer, command, doc
from gajim.command_system.implementation.hosts import ChatCommands, PrivateChatCommands, GroupChatCommands

class CustomCommonCommands(CommandContainer):
    """
    The AUTOMATIC class variable, set to a positive value, instructs the
    command system to automatically discover the command container and
    enable it.

    This command container bounds to all three available in the default
    implementation command hosts. This means that commands defined in
    this container will be available to all: chat, private chat and a
    group chat.
    """

    AUTOMATIC = True
    HOSTS = ChatCommands, PrivateChatCommands, GroupChatCommands

    @command
    def dance(self):
        """
        First line of the doc string is called a description and will be
        programmatically extracted and formatted.

        After that you can give more help, like explanation of the
        options. This one will be programatically extracted and
        formatted too.

        After all the documentation - there will be autogenerated (based
        on the method signature) usage information appended. You can
        turn it off, if you want.
        """
        return "I don't dance."

class CustomChatCommands(CommandContainer):
    """
    This command container bounds only to the ChatCommands command host.
    Therefore commands defined inside of the container will be available
    only to a chat.
    """

    AUTOMATIC = True
    HOSTS = ChatCommands,

    @command("squal", "bawl")
    def sing(self):
        """
        This command has an additional aliases. It means the command will
        be available under three names: sing (the native name), squal
        (the first alias), bawl (the second alias).

        You can turn off the usage of the native name, if you want, and
        specify a name or a set of names, as aliases, under which a
        command will be available.
        """
        return "Buy yourself a stereo."

class CustomPrivateChatCommands(CommandContainer):
    """
    This command container bounds only to the PrivateChatCommands
    command host. Therefore commands defined inside of the container
    will be available only to a private chat.
    """

    AUTOMATIC = True
    HOSTS = PrivateChatCommands,

    @command
    #Example string. Do not translate
    @doc(_("The same as using a doc-string, except it supports translation"))
    def make_coffee(self):
        return "I'm not a coffee machine!"

class CustomGroupChatCommands(CommandContainer):
    """
    This command container bounds only to the GroupChatCommands command
    host. Therefore commands defined inside of the container will be
    available only to a group chat.
    """

    AUTOMATIC = True
    HOSTS = GroupChatCommands,

    @command
    def fetch(self):
        return "Buy yourself a dog."
