'use strict';

$(function() {

    var book = $("#book");
    var mobile = window.matchMedia("(max-width: 600px)");

    if(mobile.matches)
        $("#bookbar").hide();

    PDFJS.getDocument($(document.body).data("pdf")).then(function(pdf) {
        var first_page_viewport;

        var callback = grom(function() {
            book.append('<div class="hard"></div>');
            book.append('<div class="hard"></div>');

            book.turn({
                width: first_page_viewport.width * 2,
                height: first_page_viewport.height,
                autoCenter: true
            });
        });

        for(var i = 1; i <= pdf.numPages; i++) {
            (function(i) {
                var wrapper = document.createElement("div");
                book.append(wrapper);

                function renderGraphicalPage(viewport, page) {
                    var canvas = document.createElement("canvas"),
                        _canvas = $(canvas),
                        context = canvas.getContext("2d");
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    canvas.style.backgroundColor = "#fff";
                    wrapper.appendChild(canvas);

                    _canvas.data("page", i);

                    page.render({
                        canvasContext: context,
                        viewport: viewport
                    });
                }

                function renderTextPage(viewport, page) {
                    page.getTextContent(callback.delay(function(text) {
                        var textbox = $("<div></div>");
                        textBox.addClass("textwrap");
                        textbox.text(text);
                        wrapper.append(textbox);
                    }));
                }

                pdf.getPage(i).then(callback.delay(function(page)  {

                    var viewport = page.getViewport(1);
                    // It doesn't matter if it's *actually* the first page, as long
                    // as it's the first page that we see.
                    if(!first_page_viewport)
                        first_page_viewport = viewport;

                    if(mobile.matches)
                        renderTextPage(viewport, page);
                    else
                        renderGraphicalPage(viewport, page);

                }));
            })(i);
        }

        callback.go();

    });

});