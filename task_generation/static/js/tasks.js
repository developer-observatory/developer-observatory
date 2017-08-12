$('#delModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var task_name = button.data('name'); // Extract info from data-* attributes
  var task_id = button.data('task');
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this);
  modal.find('.modal-body').text('Are you sure you want to delete \"' + task_name +'\"?');
  modal.find('.modal-footer form button').attr({'value': task_id})
});