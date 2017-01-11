var mContext = {};

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
        var data = array1[i].split('-');
        var name = data[0];
        var warn = data[1];
        var critic = data[2];
        var row = $('<tr></tr>');
        var block1 = $('<td></td>');
        block1.append(make_checkbox(true, name));
        row.append(block1);
        var block2 = $('<td></td>');
        if (warn == 'None') {
            var input_warn = $('<input class="form-control item-warn" placeholder="无">');
        } else {
            var input_warn = $('<input class="form-control item-warn" value="'+warn+'">');
        }
        block2.append(input_warn);
        row.append(block2);
        var block3 = $('<td></td>');
        if (critic == 'None') {
            var input_critic = $('<input class="form-control item-critic" placeholder="无">');
        } else {
            var input_critic = $('<input class="form-control item-critic" value="'+critic+'">');
        }
        block3.append(input_critic);
        row.append(block3);
        service_form.append(row);
    }
    for(var i = 0; i < array2.length; ++i) {
        var row = $('<tr></tr>');
        var block1 = $('<td></td>');
        block1.append(make_checkbox(false, array2[i]));
        row.append(block1);
        var block2 = $('<td><input class="form-control item-warn" placeholder="无"></td>');
        row.append(block2);
        var block3 = $('<td><input class="form-control item-critic" placeholder="无"></td>');
        row.append(block3);
        service_form.append(row);
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
            var warn = $(this).parent().parent().parent().children('td').children('.item-warn')[0].value;
            var critic = $(this).parent().parent().parent().children('td').children('.item-critic')[0].value;
            var item = {
                name: $.trim($(this).text()),
                warn: warn,
                critic: critic
            }
            selected_services.push(item);
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
    // host selected group
    var selected_grps = $('#host-'+host_id+'-group').val();
    var all_grps = $('#group_list').val();
    function make_checkbox(checked, text) {
        var str = '<div class="checkbox"><label class="group_name"><input type="checkbox" ';
        if(checked) {
            str += 'checked ';
        }
        str += '> ' + text + '</label></div>';
        return $(str)
    }

    var selected_arr = [];
    if(selected_grps) {
        selected_arr = selected_grps.split(',');
    }
    var group_arr = [];
    if(all_grps) {
        group_arr = all_grps.split(',');
    }

    var container = $('#group_selector');
    container.empty();
    for(var grp in selected_arr) {
        container.append(make_checkbox(true, selected_arr[grp]));
    }
    console.log(selected_arr);
    for(var grp in group_arr) {
        if(selected_arr.indexOf(group_arr[grp]) == -1) {
            console.log(group_arr[grp]);
            container.append(make_checkbox(false, group_arr[grp]));
        }
    }
    $('#move_group_modal').modal('show');
});
$('#move_group_modal_close').click(function() {
    $('#move_group_modal').modal('hide');
});
$('#move_group_modal_commit').click(function() {
    var selected = [];
    var labels = $('#group_selector').children('div').children('label');
    for(var i = 0; i < labels.length; ++i) {
        if($(labels[i]).children('input')[0].checked) {
            selected.push($.trim($(labels[i]).text()));
        }
    }
    var host_id = $('#move_group_modal_host_id').val();
    console.log('hostid'+host_id);
    if(selected) {
        $.ajax({
            type: 'POST',
            url: "/host-group/"+host_id+"/move",
            data: JSON.stringify({'names': selected}),
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
