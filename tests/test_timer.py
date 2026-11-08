import pytest
from timer import RestTimer


def test_rest_timer_emits_signal(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 50  # 缩短为 50ms 加速测试

    with qtbot.waitSignal(timer.rest_due, timeout=500):
        timer.start()


def test_timer_is_not_paused_initially():
    timer = RestTimer(interval_minutes=20)
    assert not timer.is_paused


def test_timer_pause_sets_paused_flag(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 100
    timer.start()
    timer.pause()

    assert timer.is_paused


def test_timer_resume_clears_paused_flag(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 100
    timer.start()
    timer.pause()
    timer.resume()

    assert not timer.is_paused


def test_timer_reset_updates_interval():
    timer = RestTimer(interval_minutes=20)
    timer.reset(10)

    assert timer._interval_ms == 10 * 60 * 1000


def test_timer_pause_prevents_signal(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 80
    timer.start()
    timer.pause()

    with qtbot.assertNotEmitted(timer.rest_due, wait=200):
        pass


def test_start_does_not_restart_a_paused_timer(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 40
    timer.start()
    timer.pause()

    timer.start()

    assert timer.is_paused
    assert not timer._timer.isActive()
    with qtbot.assertNotEmitted(timer.rest_due, wait=200):
        pass


@pytest.mark.parametrize("interval_minutes", [1, 2])
def test_reset_preserves_pause_and_resume_uses_new_interval(qtbot, interval_minutes):
    timer = RestTimer(interval_minutes=1)
    timer.start()
    timer.pause()

    timer.reset(interval_minutes)

    assert timer.is_paused
    assert not timer._timer.isActive()
    assert timer._interval_ms == interval_minutes * 60_000
    with qtbot.assertNotEmitted(timer.rest_due, wait=100):
        pass

    timer.resume()
    assert not timer.is_paused
    assert timer._timer.isActive()
    assert timer._timer.interval() == interval_minutes * 60_000
    timer.pause()


def test_pause_across_multiple_periods_then_resume_emits_again(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 40
    with qtbot.waitSignal(timer.rest_due, timeout=1000):
        timer.start()

    timer.pause()
    assert timer.is_paused
    assert not timer._timer.isActive()
    with qtbot.assertNotEmitted(timer.rest_due, wait=240):
        pass

    with qtbot.waitSignal(timer.rest_due, timeout=1000):
        timer.resume()
    assert not timer.is_paused
    assert timer._timer.isActive()
    timer.pause()


def test_paused_changed_emits_only_for_state_transitions(qtbot):
    timer = RestTimer(interval_minutes=1)
    states = []
    timer.paused_changed.connect(states.append)
    timer.start()

    timer.pause()
    timer.pause()
    timer.start()
    timer.reset(2)
    timer.resume()
    timer.resume()
    timer.pause()
    timer.pause()

    assert states == [True, False, True]
    assert timer.is_paused
    assert not timer._timer.isActive()


def test_reset_while_running_keeps_timer_running(qtbot):
    timer = RestTimer(interval_minutes=1)
    timer.start()

    timer.reset(2)

    assert not timer.is_paused
    assert timer._timer.isActive()
    assert timer._timer.interval() == 120_000
    timer.pause()
