"""Validate that all Python components have been generated."""
import sys
import dash_mui_scheduler

if __name__ == '__main__':
    print('dash_mui_scheduler version:', dash_mui_scheduler.__version__)
    print('Components:', dash_mui_scheduler.__all__)

    expected = [
        'EventCalendar', 'EventCalendarPremium', 'EventTimeline',
        'RadialLineChart', 'RadialBarChart',
    ]
    missing = [c for c in expected if not hasattr(dash_mui_scheduler, c)]
    if missing:
        print('ERROR: missing components:', missing)
        sys.exit(1)

    print('All components present: OK')
    print('Validation passed!')
