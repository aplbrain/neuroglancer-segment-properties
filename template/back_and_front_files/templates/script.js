document.addEventListener("DOMContentLoaded", function() {
    selectDatastack();
});

function selectDatastack() {
    $.get('/datastacks', function(data) {
        var datastackSelect = $('#datastackSelect');
        datastackSelect.empty(); // Clear existing options

        data.forEach(function(datastack) {
            datastackSelect.append($('<option>', {
                value: datastack,
                text: datastack
            }));
        });
    }).fail(function() {
        console.error('Failed to fetch datastacks');
    });
}

function generateUrl() {
    var datastack = $('#datastackSelect').val();
    var table = $('#tableSelect').val();
    $.post('/generate_url', { datastack: datastack, table: table }, function(response) {
        if (response.precomputed_url) {
            $('#url').attr('href', response.precomputed_url).text(response.precomputed_url);
        } else {
            alert('Error: ' + response.error);
        }
    });
}

function copyToClipboard() {
    var url = document.getElementById('url').href;
    navigator.clipboard.writeText(url).then(function() {
        alert('URL copied to clipboard!');
    }, function(err) {
        alert('Error in copying text: ', err);
    });
}
