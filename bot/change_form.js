'use strict';
document.addEventListener('DOMContentLoaded', function() {
    const inputTags = ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];
    const constantsElement = document.getElementById('django-admin-form-add-constants');
    if (constantsElement) {
        const modelName = constantsElement.dataset.modelName;
        if (modelName) {
            const form = document.getElementById(modelName + '_form');
            for (const element of form.elements) {
                if (inputTags.includes(element.tagName) && !element.disabled && element.offsetParent) {
                    element.focus();
                    break;
                }
            }
        }
    } else {
        console.error('Елемент з ID django-admin-form-add-constants не знайдено');
    }

    // Перевірка наявності елемента з ID 'add-button'
    const addButton = document.getElementById('add-button');
    if (addButton) {
        addButton.addEventListener('click', function(e) {
            e.preventDefault();

            var fieldCount = document.querySelectorAll('.button-field').length;

            var newField = document.createElement('div');
            newField.className = 'button-field';

            var buttonTextLabel = document.createElement('label');
            buttonTextLabel.setAttribute('for', 'button-text-' + (fieldCount + 1));
            buttonTextLabel.textContent = 'Button Text:';
            newField.appendChild(buttonTextLabel);

            var buttonTextInput = document.createElement('input');
            buttonTextInput.type = 'text';
            buttonTextInput.id = 'button-text-' + (fieldCount + 1);
            buttonTextInput.name = 'button-text';
            newField.appendChild(buttonTextInput);

            var buttonLinkLabel = document.createElement('label');
            buttonLinkLabel.setAttribute('for', 'button-link-' + (fieldCount + 1));
            buttonLinkLabel.textContent = 'Button Link:';
            newField.appendChild(buttonLinkLabel);

            var buttonLinkInput = document.createElement('input');
            buttonLinkInput.type = 'text';
            buttonLinkInput.id = 'button-link-' + (fieldCount + 1);
            buttonLinkInput.name = 'button-link';
            newField.appendChild(buttonLinkInput);

            document.getElementById('post-buttons').appendChild(newField);
        });
    } else {
        console.error('Елемент з ID add-button не знайдено');
    }
});
