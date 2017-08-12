original_condition_states = {};

$('.condition-box').change(function () {
    var box_id = this.id;
    if (box_id in original_condition_states) {
        var returned = true;
        Object.keys(original_condition_states).forEach(function (b_id) {
            var is_checked = $('#' + b_id).prop('checked');
            returned &= original_condition_states[b_id] === is_checked
        });
        if (returned) {
            $('#txt-refresh').hide();
            $('#btn-generate').prop('disabled', false);
        }
        else {
            disable()
        }
    }
    else {
        original_condition_states[box_id] = !this.checked;
        disable()
    }
});

function disable() {
    $('#txt-refresh').show();
    $('#btn-generate').prop('disabled', true);
}