(function($) {
    $(document).ready(function() {
        var $messageType = $('#id_message_type');
        var $mediaFileField = $('.field-media_file').parent('.form-row');
        var $mediaInline = $('.inline-group').filter(function() {
            return $(this).find('.inline-related').first().hasClass('post-media-content');
        });

        function toggleFields() {
            var selectedType = $messageType.val();
            
            if (selectedType === 'text') {
                $mediaFileField.hide();
                $mediaInline.hide();
            } else if (selectedType === 'media_group') {
                $mediaFileField.hide();
                $mediaInline.show();
            } else {
                $mediaFileField.show();
                $mediaInline.hide();
            }
        }

        $messageType.change(toggleFields);
        toggleFields(); // Викликаємо одразу для встановлення початкового стану
    });
})(django.jQuery); 