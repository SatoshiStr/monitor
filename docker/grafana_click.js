
$(function(){
    $(document).on('click', '.singlestat-panel', function(){
        var row = $(this);
        for(var i = 0; i < 9; ++i) {
            row = row.parent();
        }
        var header = row.children('.dash-row-header').children('.dash-row-header-title').children('.h6').text();
        console.log(header);
        var items = location.href.split('/');
        var item = items[items.length-1];
        if(item.slice(0,6) == 'zhu-ji' || item == 'quan-bu-zhu-ji') {
            location.href = '/dashboard/db/zhu-ji-' + header;
        } else {
            location.href = '/dashboard/db/vm-' + header;
        }
    });
});
