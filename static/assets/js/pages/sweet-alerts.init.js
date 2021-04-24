!(function (t) {
    "use strict";
    var e = function () {};
    (e.prototype.init = function () {
            t(".sa-params").click(function () {
                Swal.fire({
                    title: "Tên bệnh nhân",
                    text: "Thông tin bệnh nhân",
                    type: "warning",
                    showCancelButton: !0,
                    confirmButtonText: "Xác nhận hẹn",
                    cancelButtonText: "Hủy hẹn",
                    confirmButtonClass: "btn btn-success mt-2",
                    cancelButtonClass: "btn btn-danger ml-2 mt-2",
                    buttonsStyling: !1,
                }).then(function (t) {
                    t.value
                        ? Swal.fire({ title: "Đã xác nhận!", text: "Bệnh nhân đã lên lịch khám thành công.", type: "success" })
                        : t.dismiss === Swal.DismissReason.cancel && Swal.fire({ title: "Đã hủy!", text: "Đã hủy lịch hẹn của bệnh nhân.", type: "error" });
                });
            });
    }),
        (t.SweetAlert = new e()),
        (t.SweetAlert.Constructor = e);
})(window.jQuery),
    (function (t) {
        "use strict";
        window.jQuery.SweetAlert.init();
    })();
