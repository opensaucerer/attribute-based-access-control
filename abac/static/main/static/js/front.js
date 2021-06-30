$(function () {


    $('#searchToggler').on('click', function (e) {
        e.preventDefault();
        $(this).find('.fa-search, .fa-times').toggleClass('d-none');
        $('#search').toggleClass('active');
    });

});
