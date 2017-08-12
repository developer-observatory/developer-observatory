$('#delModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var name = button.data('name'); // Extract info from data-* attributes
  var id = button.data('id');
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this);
  modal.find('.modal-body').text('Are you sure you want to delete \"' + name +'\"?');
  modal.find('.modal-footer form button').attr({'value': id})
});