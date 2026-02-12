import runpy
import pandas as pd
from unittest.mock import patch, MagicMock
from src.siegfried.hunt import (
    z_score, daily_returns, detect_anomaly,
    find_anomalies, report, hunt_unusual_movers,
    opening_gap,
)


def make_returns(values):
    return pd.Series(values)


def make_history(open_prices, close_prices):
    return pd.DataFrame({"Open": open_prices, "Close": close_prices})


class TestZScore:
    def test_positive_z_score(self):
        returns = make_returns([0.01, 0.01, 0.01, 0.01, 0.10])
        z = z_score(returns)
        assert z > 0

    def test_negative_z_score(self):
        returns = make_returns([0.01, 0.01, 0.01, 0.01, -0.10])
        z = z_score(returns)
        assert z < 0

    def test_near_zero_z_when_last_near_mean(self):
        returns = make_returns([0.05, 0.04, 0.06, 0.05, 0.05])
        z = z_score(returns)
        assert abs(z) < 0.5


class TestOpeningGap:
    def test_computes_open_vs_previous_close(self):
        hist = make_history(
            open_prices=[100, 105, 110],
            close_prices=[102, 108, 112],
        )
        gaps = opening_gap(hist)
        assert len(gaps) == 2
        assert abs(gaps.iloc[0] - (105 / 102 - 1)) < 1e-10
        assert abs(gaps.iloc[1] - (110 / 108 - 1)) < 1e-10


class TestDailyReturns:
    @patch("src.siegfried.hunt.yf")
    def test_returns_none_when_too_few_days(self, mock_yf):
        mock_yf.Ticker.return_value.history.return_value = make_history([100, 101], [100, 101])
        assert daily_returns("XYZ", min_days=30) is None

    @patch("src.siegfried.hunt.yf")
    def test_returns_series_when_enough_days(self, mock_yf):
        close_prices = list(range(100, 140))
        open_prices = [c + 1 for c in close_prices]
        mock_yf.Ticker.return_value.history.return_value = make_history(open_prices, close_prices)
        result = daily_returns("XYZ", min_days=30)
        assert result is not None
        assert len(result) == 39  # 40 rows → 39 gaps after dropna


class TestDetectAnomaly:
    @patch("src.siegfried.hunt.daily_returns", return_value=None)
    def test_returns_none_when_no_history(self, _):
        assert detect_anomaly("XYZ", 1.5) is None

    @patch("src.siegfried.hunt.daily_returns")
    def test_returns_none_when_below_threshold(self, mock_dr):
        mock_dr.return_value = make_returns([0.01, 0.02, 0.01, 0.02, 0.015])
        assert detect_anomaly("XYZ", 1.5) is None

    @patch("src.siegfried.hunt.daily_returns")
    def test_returns_tuple_when_above_threshold(self, mock_dr):
        mock_dr.return_value = make_returns([0.01, 0.01, 0.01, 0.01, 0.50])
        result = detect_anomaly("XYZ", 1.5)
        assert result is not None
        sym, chg, z = result
        assert sym == "XYZ"
        assert chg == 0.50 * 100
        assert abs(z) >= 1.5

    @patch("src.siegfried.hunt.daily_returns")
    def test_detects_negative_anomaly(self, mock_dr):
        mock_dr.return_value = make_returns([0.01, 0.01, 0.01, 0.01, -0.50])
        result = detect_anomaly("XYZ", 1.5)
        assert result is not None
        _, _, z = result
        assert z < 0


class TestFindAnomalies:
    @patch("src.siegfried.hunt.detect_anomaly")
    def test_collects_only_anomalies(self, mock_detect):
        mock_detect.side_effect = [None, ("B", 5.0, 2.0), None, ("D", -3.0, -1.8)]
        result = find_anomalies(["A", "B", "C", "D"], 1.5)
        assert len(result) == 2
        assert result[0][0] == "B"
        assert result[1][0] == "D"

    @patch("src.siegfried.hunt.detect_anomaly", return_value=None)
    def test_returns_empty_when_no_anomalies(self, _):
        assert find_anomalies(["A", "B"], 1.5) == []


class TestReport:
    def test_prints_hits(self, capsys):
        report([("VZ", 3.21, 2.10), ("SPY", -2.50, -1.80)])
        out = capsys.readouterr().out
        assert "VZ" in out
        assert "+3.21%" in out
        assert "SPY" in out
        assert "-2.50%" in out

    def test_prints_nothing_unusual_when_empty(self, capsys):
        report([])
        out = capsys.readouterr().out
        assert "nothing unusual" in out


class TestHuntUnusualMovers:
    @patch("src.siegfried.hunt.report")
    @patch("src.siegfried.hunt.find_anomalies", return_value=[("VZ", 3.0, 2.0)])
    def test_calls_find_then_report(self, mock_find, mock_report):
        hunt_unusual_movers(["VZ"], 1.5)
        mock_find.assert_called_once_with(["VZ"], 1.5)
        mock_report.assert_called_once_with([("VZ", 3.0, 2.0)])


class TestMain:
    @patch("yfinance.Ticker")
    def test_main_entry_point(self, mock_ticker, capsys):
        close_prices = list(range(100, 140))
        open_prices = [c + 1 for c in close_prices]
        mock_ticker.return_value.history.return_value = make_history(open_prices, close_prices)
        runpy.run_module("src.siegfried.hunt", run_name="__main__")
        out = capsys.readouterr().out
        assert out.strip()
