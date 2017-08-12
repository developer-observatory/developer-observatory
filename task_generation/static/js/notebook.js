$('.taskbox').change(function () {
    var box_class = 'optiontask-' + this.value;
    if (this.checked) {
        $('.' + box_class).show();
    } else {
        $('.' + box_class).hide().find('input').prop('checked', false);
    }
});

$('.typeselector').change(function () {
    $(this).parent().next().find("div").hide();
    if (this.value === 'fixed') {
        $(this).parent().next().find('.tasks-fixed').show();
    }
    if (this.value === 'random') {
        $(this).parent().next().find('.tasks-random').show();
    }
});

function addOption() {
    var numOptions = $('tbody tr').length;

    var lastRow = $('tr:last');
    var newRow = lastRow.clone(true);

    var select_id = 'order_options-' + numOptions + '-order_type';
    var fixed_name = 'order_options-' + numOptions + '-tasks_fixed';
    var random_name = 'order_options-' + numOptions + '-tasks_random';

    newRow.find('td:first').text(numOptions+1);
    newRow.find('select').attr({id: select_id, name: select_id}).val(lastRow.find('select').val());

    newRow.find('div.tasks-fixed input').each(function (index) {
        $(this).attr({name: fixed_name, id: fixed_name + '-' + index}).prop('checked', false);
    });

    newRow.find('div.tasks-random input').each(function (index) {
        $(this).attr({name: random_name, id: random_name + '-' + index}).prop('checked', false);
    });


    lastRow.after(newRow);

    // show remove button
    $('#btnRemove').show()


}

function removeOption() {
    var numOptions = $('tbody tr').length;
    if(numOptions > 1){
        if(numOptions === 2){
            $('#btnRemove').hide();
        }
        $('tbody tr:last').remove();
    }
}