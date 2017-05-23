var clipboard = new Clipboard('#copyurl');


var app = new Vue({
    delimiters: ['${', '}'],
    el: '#app',
    data: {
        custom: '',
        url: '',
        shortenButton: true,
        copyButton: false,
        errors: [],
        successMessage: ''

    },
    methods: {
        shorten: function () {
            var csrftoken = $('[name="csrfmiddlewaretoken"]').val();
            var config = {
                headers: {"X-CSRFToken": csrftoken}
            };
            var vm = this;
            axios.post('short', {
                url: vm.url,
                custom: vm.custom
            }, config)
                .then(function (response) {
                    vm.url = response.data.url;
                    vm.shortenButton = false;
                    vm.copyButton = true;
                    vm.errors = [];
                    vm.successMessage = "URL has been successfully shortened. " +
                        "If you want to try another one please either click Copy button or delete the current URL";
                })
                .catch(function (error) {
                    vm.errors = error.data.errors;
                    vm.error = true;
                    vm.success = false;
                    vm.successMessage = ''
                })
        },

        afterCopy: function () {
            var vm = this;
            vm.shortenButton = true;
            vm.copyButton = false;
            vm.errors = [];
            vm.url = '';
            vm.successMessage = "URL has been copied to your clipboard"
        }
    },

    watch: {
        url: function (val) {
            if (val === '') {
                var vm = this;
                vm.shortenButton = true;
                vm.copyButton = false;
                vm.errors = [];
                vm.successMessage = '';
            }
        }
    }
});


clipboard.on('success', function () {
    app.afterCopy();
});