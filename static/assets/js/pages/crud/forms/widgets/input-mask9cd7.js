// Class definition

var KTInputmask = function () {
    
    // Private functions
    var demos = function () {
        // currency format
        $(".kt_inputmask_7").inputmask('VND 999.999.999', {
            numericInput: true
        }); //123456  =>  € ___.__1.234,56
    }

    return {
        // public functions
        init: function() {
            demos(); 
        }
    };
}();

jQuery(document).ready(function() {
    KTInputmask.init();
});