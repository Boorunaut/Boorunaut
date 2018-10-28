$(function() {
    $('.tag-search').tagsInput({
        'autocomplete_url': tag_search_url,
        'delimiter': [' '],   // Or a string with a single delimiter. Ex: ';'
        'width': '100%',
        'height': '45px',
    });

    $('#tags_tagsinput').addClass("col-md-9");

    $('#id_tags').tagsInput({
        'autocomplete_url': tag_search_url,
        'delimiter': [' '],   // Or a string with a single delimiter. Ex: ';'
        'height': '100%',
        'width': '100%'
    });

    let searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('tags')){
        let tags = searchParams.get('tags');
        $('.tag-search').importTags(tags);
    }    
});