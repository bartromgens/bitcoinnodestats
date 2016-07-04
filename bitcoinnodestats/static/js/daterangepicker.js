$(function() {

    var dateFormatInput = 'YYYY-MM-DD';
    var dateFormatInterface = 'D MMMM YYYY';

    function getURLParameter(name) {
      return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
    }

    var dateBegin = getURLParameter('date_begin');
    var dateEnd = getURLParameter('date_end');
    var binSizeHours = getURLParameter('bin_size_hour');
    console.log(dateBegin);
    console.log(dateEnd);
    console.log(binSizeHours);

    function cb(start, end, changeUrl=true) {
        $('#reportrange span').html(start.format(dateFormatInterface) + ' - ' + end.format(dateFormatInterface));
        console.log(start.format(dateFormatInput));
        console.log(end.format(dateFormatInput));
        if (changeUrl) {
            var newUrl = '/?date_begin=' + start.format('YYYY-MM-DD');
            newUrl += '&date_end=' + end.format('YYYY-MM-DD')
            window.location.href = newUrl;
        }
    }

    var momentBegin = moment().subtract(29, 'days');
    if (dateBegin) {
        momentBegin = moment(dateBegin, dateFormatInput);
    }
    var momentEnd = moment();  // default is now
    if (dateEnd) {
        momentEnd = moment(dateEnd, dateFormatInput);
    }

    cb(momentBegin, momentEnd, false);

    $('#reportrange').daterangepicker({
        ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }, cb);

});