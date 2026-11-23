""".fms 解析器测试（fixture 取自真实 X-Plane / SimBrief 文件）。"""
import pytest

from core.navigation.fms_parser import FmsParseError, parse_fms

NEW_FMS = """I
1100 Version
CYCLE 2503
ADEP ZBAA
DEPRWY RW18L
SID RUSD6J
ADES ZUGY
DESRWY RW19L
STAR MEMA7X
NUMENR 23
1 ZBAA ADEP 116.000000 40.073333 116.598333
11 RUSDO DRCT 34300.000000 39.761111 115.447500
11 ADPUM W45 36000.000000 39.385556 114.510556
"""

# SimBrief 下载的 .fms：只有跑道，没有 SID/STAR
SIMBRIEF_FMS = """I
1100 Version
CYCLE 2503
ADEP ZUUU
DEPRWY RW20R
ADES ZUGY
DESRWY RW19L
NUMENR 15
1 ZUUU ADEP 1681.000000 30.580000 103.948333
3 CTU DRCT 3200.000000 30.573333 103.943333
3 BHS W237 13200.000000 30.511667 104.200000
11 IPLOL W237 24400.000000 30.139444 104.410000
"""

OLD_FMS = """ZUGY
ZBAD
DIRECT
AVBOB
W586
TRN
W183
HUY
A581
IDPOG
W56
ORODO
W62
TEKIL
G212
BELAX
99
"""


def test_parse_new_format():
    plan = parse_fms(NEW_FMS)
    assert plan.departure == "ZBAA"
    assert plan.destination == "ZUGY"
    assert plan.departure_runway == "RW18L"
    assert plan.arrival_runway == "RW19L"
    assert plan.sid == "RUSD6J"
    assert plan.star == "MEMA7X"
    assert plan.cycle == "2503"
    assert len(plan.waypoints) == 3

    w0 = plan.waypoints[0]
    assert w0.ident == "ZBAA"
    assert w0.type == "APT"
    assert w0.airway == "ADEP"
    assert w0.altitude_ft == pytest.approx(116.0)

    w1 = plan.waypoints[1]
    assert w1.ident == "RUSDO"
    assert w1.type == "FIX"
    assert w1.airway == "DRCT"
    assert w1.altitude_ft == pytest.approx(34300.0)

    w2 = plan.waypoints[2]
    assert w2.ident == "ADPUM"
    assert w2.airway == "W45"
    assert w2.latitude == pytest.approx(39.385556)


def test_parse_simbrief_without_sid_star():
    plan = parse_fms(SIMBRIEF_FMS)
    assert plan.departure == "ZUUU"
    assert plan.destination == "ZUGY"
    assert plan.departure_runway == "RW20R"
    assert plan.arrival_runway == "RW19L"
    assert plan.sid is None
    assert plan.star is None
    assert plan.cycle == "2503"
    assert plan.waypoints[0].type == "APT"
    assert plan.waypoints[1].ident == "CTU"
    assert plan.waypoints[1].type == "VOR"


def test_parse_old_format():
    plan = parse_fms(OLD_FMS)
    assert plan.departure == "ZUGY"
    assert plan.destination == "ZBAD"
    assert plan.sid is None
    assert len(plan.waypoints) == 7

    assert plan.waypoints[0].ident == "AVBOB"
    assert plan.waypoints[0].airway == "W586"
    assert plan.waypoints[1].ident == "TRN"
    assert plan.waypoints[1].airway == "W183"
    assert plan.waypoints[-1].ident == "BELAX"
    assert plan.waypoints[-1].airway == "DRCT"  # 最后一个航路点无后续航路


def test_parse_empty_raises():
    with pytest.raises(FmsParseError):
        parse_fms("")
