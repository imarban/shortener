var app = new Vue({
    delimiters: ['${', '}'],
    el: '#app',
    data: {
        shortened: '',
        custom: '',
        url: '',
        success: false,
        error: false,
        errors: []

    },
    methods: {
        shorten: function () {
            var csrftoken = $('[name="csrfmiddlewaretoken"]').val();
            var config = {
                headers: {"X-CSRFToken": csrftoken}
            };
            var vm = this;
            console.log(vm.url);
            console.log(vm.custom);
            axios.post('short', {
                url: vm.url,
                custom: vm.custom
            }, config)
                .then(function (response) {
                    vm.shortened = response.data.shortened;
                    vm.url = response.data.url;
                    vm.success = true;
                    vm.error = false;
                })
                .catch(function (error) {
                    console.log(error.data.errors);
                    vm.errors = error.data.errors;

                    vm.error = true;
                    vm.success = false;
                    vm.answer = 'Error! Could not reach the API. ' + error
                })
        }
    }
});

