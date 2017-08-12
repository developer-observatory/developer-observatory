function addCell(){
    // count how many cell fields we have
    var numCells = $('.cell-field').length;

    // duplicate last field
    var div = $('.cell-field:last');
    var div2 = div.clone();

    // set correct ids
    var newId = 'cells-'+numCells;
    div2.find('label').attr('for', newId);
    div2.find('label').text('Cell '+(numCells+1));
    div2.find('select').attr({id: newId, name: newId});

    div.after(div2);

    // show remove button
    $('#btnRemove').show()

}

function removeCell(){
    // count how many cell fields we have
    var numCells = $('.cell-field').length;

    // if we have more than one we can remove one
    if(numCells > 1){
        //if there are only two left we hide the button
        if(numCells === 2){
            $('#btnRemove').hide()
        }
        // remove last cell form
        $('.cell-field:last').remove();
    }
}