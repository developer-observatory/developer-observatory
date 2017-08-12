function addKeyValue(){
    // get number of existing metadata key fields
    var numPairs = $('.pair-key').length;

    // get last key and value form elements
    var k = $('.pair-key:last');
    var v = $('.pair-value:last');

    // clone elements
    var k2 = k.clone();
    var v2 = v.clone();

    // clear values
    k2.children().each(function(){
       $( this ).val('');
    });

    v2.children().each(function(){
        $( this ).val('');
    });

    // replace for attributes of labels and ids of input fields
    var keyId = 'pairs-'+numPairs+'-key';
    var valId = 'pairs-'+numPairs+'-value';

    k2.find('label').attr('for', keyId);
    v2.find('label').attr('for', valId);

    k2.find('input').attr({id: keyId, name: keyId});
    v2.find('input').attr({id: keyId, name: valId});

    // append cloned elements
    v.after(k2);
    k2.after(v2);

    // show remove button
    $('#btnRemove').show()
}

function removeKeyValue(){

    // count how many fields we have
    var numFields = $('.pair-key').length;

    // if we have more than one we can remove one
    if(numFields > 1){
        //if there are only two left we hide the button
        if(numFields === 2){
            $('#btnRemove').hide()
        }
        // remove last key-value fields
        $('.pair-key:last').remove();
        $('.pair-value:last').remove();
    }
}
