$(function() {
    $('#tags').tagsInput({
        'autocomplete_url': tag_search_url,
        'delimiter': [' '],   // Or a string with a single delimiter. Ex: ';'
        'height': '100%',
    });

    $('#id_tags').tagsInput({
        'autocomplete_url': tag_search_url,
        'delimiter': [' '],   // Or a string with a single delimiter. Ex: ';'
        'height': '100%',
        'width': '100%'
    });
});