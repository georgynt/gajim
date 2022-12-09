from unittest.mock import MagicMock

from gi.repository import Gio
from gi.repository import Gtk

from gajim import gui
gui.init('gtk')
from gajim.common import app
from gajim.common.const import CSSPriority

from gajim.gui.ssl_error_dialog import SSLErrorDialog

from . import util

util.load_style('gajim.css', CSSPriority.APPLICATION)

cert = '''
-----BEGIN CERTIFICATE-----
MIIFhDCCBGygAwIBAgISA4oUEifTr7Y+mcdiwu6KWpcVMA0GCSqGSIb3DQEBCwUA
MEoxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MSMwIQYDVQQD
ExpMZXQncyBFbmNyeXB0IEF1dGhvcml0eSBYMzAeFw0xOTA0MDMxODE3NDVaFw0x
OTA3MDIxODE3NDVaMBsxGTAXBgNVBAMMECoubGlnaHR3aXRjaC5vcmcwggEiMA0G
CSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC/3mcevikse7QwDYwPcGAD9zHw3UWE
7J8SJR349/rFTF2tBFDvEa62OUKTCg5vPKVKaXHlzruk/A7blgqsEdugycORwPD1
7YNJ27EldrRtotjclurzKL6D/MgcaQ4cTkPOD3cWbf/L+HClGrpFt7su6Z6cTutC
wiAYAdlfmVgSSv15F1xOTyFyfGJKQnW628Xs8xUvZh5H/SsEEum4MwVVGW06Z/A/
mwX2jmJUb2M25S1Ma025nZpGYyAAqecTmPb3fStnXm4sdytfZhm4+nj9mH9GQIU1
t/jO/7X7IFpc9DvVRSumSVqvNaVgiWmTLP4VxlCVJO6mibOXXUUDA5RfAgMBAAGj
ggKRMIICjTAOBgNVHQ8BAf8EBAMCBaAwHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsG
AQUFBwMCMAwGA1UdEwEB/wQCMAAwHQYDVR0OBBYEFC4/ZRurw2wVFsgJBTb9Fh/3
0aV9MB8GA1UdIwQYMBaAFKhKamMEfd265tE5t6ZFZe/zqOyhMG8GCCsGAQUFBwEB
BGMwYTAuBggrBgEFBQcwAYYiaHR0cDovL29jc3AuaW50LXgzLmxldHNlbmNyeXB0
Lm9yZzAvBggrBgEFBQcwAoYjaHR0cDovL2NlcnQuaW50LXgzLmxldHNlbmNyeXB0
Lm9yZy8wSQYDVR0RBEIwQIIQKi5saWdodHdpdGNoLm9yZ4IOKi5tZXRyb25vbWUu
aW2CDmxpZ2h0d2l0Y2gub3JnggxtZXRyb25vbWUuaW0wTAYDVR0gBEUwQzAIBgZn
gQwBAgEwNwYLKwYBBAGC3xMBAQEwKDAmBggrBgEFBQcCARYaaHR0cDovL2Nwcy5s
ZXRzZW5jcnlwdC5vcmcwggECBgorBgEEAdZ5AgQCBIHzBIHwAO4AdQB0ftqDMa0z
EJEhnM4lT0Jwwr/9XkIgCMY3NXnmEHvMVgAAAWnkosBAAAAEAwBGMEQCICEfmTBk
OxS95eiYsfTH5HdL7kfp68BSin5LqeGyyxk9AiA3qeDZNKklJTdWqYjto7kUqJNd
YiL99SrqwzR6w+AqSwB1ACk8UZZUyDlluqpQ/FgH1Ldvv1h6KXLcpMMM9OVFR/R4
AAABaeSiwEUAAAQDAEYwRAIgFxouOkJeqkQUe6zNI5w/6YBIQFrsrIZdPcX+r6JI
is8CIEEETzlEyj9lWR/BSSruSp0FT5CuoNNeEG7HxrJ+gVhZMA0GCSqGSIb3DQEB
CwUAA4IBAQAQtfs1NPNMmBQRcKsZyGLZsvpp2hIhdYi72RYnHnIl4MXbhyNj9xtI
cJr9PQ+3FsSnxy7LDjZMpbmBuXhawOyPBPw2M0f0Tv6Eo6miwvP/X1kLE3VjTzCo
6JPh6bEB5wa+kH/pUcGlV6uyT7IuXOiArx0VmIpTA3uwlVdfynOnR3CF20Ds4FLc
JxbGMqRuw/sGiTLKlXc1xVil8WZjL3hokzrgI7K6np2skUjWuMZvhJgwi5QiE7/C
ejsJoYkpvcaiaLAyVymTY/n/oM2oQpv5Mqjit+18RB9c2P+ifH5iDKC/jTKn4NNz
8xSTlUlCBTCozjzscZVeVDIojmejWclT
-----END CERTIFICATE-----'''


app.settings = MagicMock()
app.settings.get_account_setting = MagicMock(
    return_value=['myhost@example.tld'])

gio_cert = Gio.TlsCertificate.new_from_pem(cert, -1)
ssl_error_num = 10
win = SSLErrorDialog('testacc', None, gio_cert, ssl_error_num)
win.connect('destroy', Gtk.main_quit)
win.show_all()
Gtk.main()
