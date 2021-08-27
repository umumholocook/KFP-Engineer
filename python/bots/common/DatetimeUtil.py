import calendar
from datetime import datetime, timedelta, timezone

from .SimpleDiscordMarkdown.Datatypes import TimestampStyle

_WEEKDAY_L10N = '一二三四五六日'

_STYLEFORMAT = {
    TimestampStyle.SHORT_TIME:
        '{0:%H:%M}',
    TimestampStyle.LONG_TIME:
        '{0:%X}',
    TimestampStyle.SHORT_DATE:
        '{0:%Y/%M/%d}',
    TimestampStyle.LONG_DATE: 
        '{0.year}年{0.month}月{0.day}日',
    TimestampStyle.SHORT_DATETIME:
        '{0.year}年{0.month}月{0.day}日 {0:%H:%M}',
    TimestampStyle.LONG_DATETIME:
        '{0.year}年{0.month}月{0.day}日星期{weekday} {0:%H:%M}',
}

_TIMEFRAME_L10N = ['年', '個月', '天', '小時', '分鐘']
_TIMEFRAME_LENGTH = [
    lambda d: 12,
    lambda d: calendar.monthrange(d.year, d.month)[1],
    lambda d: 24,
    lambda d: 60,
    lambda d: 60,
]

def strptime(timestamp, style: TimestampStyle, tz=timezone(timedelta(hours=8)),
             *, origintimestamp=None) -> str:
    # 有可能有不合理的時間
    try:
        dttm = datetime.fromtimestamp(timestamp, tz=tz)
        if style == TimestampStyle.RELATIVE_TIME:
            origin = datetime.fromtimestamp(origintimestamp, tz=tz)
    except (OverflowError, OSError):
        return 'Invalid date'
    
    if style == TimestampStyle.RELATIVE_TIME:
        if dttm > origin :
            position = '內'
            future, past = dttm, origin
        else:
            position = '前'
            future, past = origin, dttm
        f = future.timetuple()
        p = past.timetuple()
        
        # 借位
        borrow = 0
        for i in range(5):
            # 如果 delta > 1，代表前後以此時間尺度衡量的差異夠大
            # delta == 1 的話，前後時間差異可能不足此時間尺度的單位
            delta = f[i] - p[i] + borrow
            if delta > 1 or delta == 1 and f[i+1] >= p[i+1]:
                return f'{delta} {_TIMEFRAME_L10N[i]}{position}'
            elif delta == 1:
                borrow = _TIMEFRAME_LENGTH[i](past)
            
        return f'幾秒鐘{position}'
    
    return _STYLEFORMAT[style].format(dttm, weekday=_WEEKDAY_L10N[dttm.weekday()])
    