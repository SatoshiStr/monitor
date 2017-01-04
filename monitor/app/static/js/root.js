$('.show_service_modal').click(function() {
    function make_checkbox(checked, text) {
        var str = '<div class="checkbox"><label class="monitor_item_name"><input type="checkbox" ';
        if(checked) {
            str += 'checked ';
        }
        str += '> ' + text + '</label></div>';
        return $(str)
    }

    var service_form = $('#service_form');
    service_form.empty();
    var host_id_input = $('#service_host_id');
    host_id_input.val($(this).next().next().val());
    var data = $(this).next().val().split(';');
    if(data[0] == '') {
        var array1 = [];
    } else {
        var array1 = data[0].split(',');
    }
    if(data[1] == '') {
        var array2 = [];
    } else {
        var array2 = data[1].split(',');
    }
    for(var i = 0; i < array1.length; ++i) {
        service_form.append(make_checkbox(true, array1[i]));
    }
    for(var i = 0; i < array2.length; ++i) {
        service_form.append(make_checkbox(false, array2[i]));
    }
    $('#service_modal').modal('show');
});

$('#service_modal_close').click(function() {
    $('#service_modal').modal('hide');
});

$('#service_modal_submit').click(function() {
    $('#service_modal').modal('hide');
    selected_services = []
    $('.monitor_item_name').each(function() {
        if($(this).children('input')[0].checked) {
            selected_services.push($.trim($(this).text()));
        }
    });
    var host_id = $('#service_host_id').val();
    $.ajax({
        type: 'POST',
        url: "/host/"+host_id+"/service",
        data: JSON.stringify(selected_services),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            location.reload();
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
});

$('#add_host').click(function() {
    $('#host_modal').modal('show');
});

$('#host_modal_close').click(function() {
    $('#host_modal').modal('hide');
});

$('#host_modal_submit').click(function() {
    $('#host_modal').modal('hide');
});

$('.remove_host').click(function() {
    var host_id = $($(this).parent().parent().children('td')[0]).text();
    $.ajax({
        type: 'POST',
        url: "/host/"+host_id+"/remove",
        data: '{}',
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            location.reload();
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
});

$('.config_host').click(function() {
    var host_id = $($(this).parent().parent().children('td')[0]).text();
    $.ajax({
        type: 'POST',
        url: "/host/"+host_id+"/config",
        data: '{}',
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            location.reload();
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
});

$('.config_detail').click(function() {
    var host_id = $($(this).parent().parent().children('td')[0]).text();
    $.ajax({
        type: 'GET',
        url: "/host/"+host_id+"/config-detail",
        data: null,
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            $('#config_stdout').text(data['stdout']);
            $('#config_modal').modal('show');
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
});

$('#config_modal_close').click(function() {
    $('#config_modal').modal('hide');
});


// group detail
$('#add_multiple_host').click(function() {
    $('#multi_host_modal').modal('show');
});
$('#multi_host_modal_close').click(function() {
    $('#multi_host_modal').modal('hide');
});
// 移动主机
$('.show_group_modal').click(function() {
    var host_id = $($(this).parent().parent().children('td')[0]).text();
    $('#move_group_modal_host_id').val(host_id);
    $('#move_group_modal').modal('show');
});
$('#move_group_modal_close').click(function() {
    $('#move_group_modal').modal('hide');
});
$('#move_group_modal_commit').click(function() {
    var content = null;
    var labels = $('#group_selector').children('div').children('label');
    for(var i = 0; i < labels.length; ++i) {
        if($(labels[i]).children('input')[0].checked) {
            var content = $.trim($(labels[i]).text()).slice(5);
            break;
        }
    }
    var host_id = $('#move_group_modal_host_id').val();
    console.log('hostid'+host_id);
    if(content !== null) {
        $.ajax({
            type: 'POST',
            url: "/host-group/"+host_id+"/move",
            data: JSON.stringify({'name': content}),
            contentType: 'application/json; charset=UTF-8',
            dataType: 'json',
            success: function (data) {
                location.reload();
            },
            error: function (xhr, type) {
                console.log("提交数据失败！");
                console.log(xhr);
                console.log(type);
            }
        });
        $('#move_group_modal').modal('hide');
    }

});
// 主机组服务
$('#show_group_service').click(function() {
    $('#group_service_modal').modal('show');
});
$('#group_service_modal_close').click(function() {
    $('#group_service_modal').modal('hide');
});
$('#group_service_modal_submit').click(function() {
    selected_services = []
    $('.monitor_item_name').each(function() {
        if($(this).children('input')[0].checked) {
            selected_services.push($.trim($(this).text()));
        }
    });
    var host_id = $('#service_group_id').val();
    $.ajax({
        type: 'POST',
        url: "/host-group/"+host_id+"/service",
        data: JSON.stringify(selected_services),
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            location.reload();
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
    $('#group_service_modal').modal('hide');
});
// 配置所有主机组
$('#config_all_host').click(function() {
    var group_id = $('#service_group_id').val();
    $.ajax({
        type: 'POST',
        url: "/host-group/"+group_id+"/config",
        data: '{}',
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            location.reload();
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
});

// 同步
$('#sync').click(function() {
    $.ajax({
        type: 'POST',
        url: "/sync",
        data: '{}',
        contentType: 'application/json; charset=UTF-8',
        dataType: 'json',
        success: function (data) {
            location.reload();
        },
        error: function (xhr, type) {
            console.log("提交数据失败！");
            console.log(xhr);
            console.log(type);
        }
    });
});
