mypy -p gajim.common.modules --follow-imports=skip
pylint --jobs=2 --additional-builtins=_ --disable=all --enable=C0121,C0201,C0303,C0321,C0325,C0326,C1801,E0001,E0011,E0012,E0100,E0101,E0102,E0103,E0104,E0105,E0106,E0107,E0108,E0202,E0221,E0222,E0235,E0501,E0502,E0503,E0602,E0603,E0604,E0701,E0702,E1001,E1002,E1003,E1004,E1111,E1120,E1121,E1122,E1123,E1124,E1125,E1200,E1201,E1205,E1206,E1300,E1301,E1302,E1303,E1304,E1305,E1306,E1310,E1700,E1701,R0123,R0205,R1703,R1704,R1705,R1707,W0102,W0611,W0612,W0621,W0622,W0702,W1201,W1202 gajim
