'use strict';

var page_width = -1;

var book = document.getElementById("book"),
    mobile = window.matchMedia("(max-width: 600px)");

if(mobile.matches)
    document.getElementById("bookbar").style.display = "none";

PDFJS.getDocument(document.body.getAttribute("data-pdf")).then(function(pdf) {
    var first_page_viewport,
        is_text = true;

    var callback = grom(function() {
        var back_cover = document.createElement("div");
        back_cover.className = "cover";
        back_cover.innerHTML = "Powered by Web Books";
        book.appendChild(back_cover);

        page_width = first_page_viewport.width;

        if(!is_text) {
            $("#book .page, #book .cover").each(function(i, e) {
                e.style.height = first_page_viewport.height + "px";
                e.style.width = first_page_viewport.width + "px";
            });

            book.style.height = first_page_viewport.height + "px";
            book.style.width = first_page_viewport.width + "px";
            book.className += " graphical";
        } else
            book.className += " textual";
        bastaflip_grom.go();

    });

    var fold;
    for(var i = 1; i <= pdf.numPages; i++) {
        if(i % 2 == 1) {
            fold = document.createElement("div");
            fold.className = "fold";
            book.appendChild(fold);
        }
        (function(fold, i) {
            var wrapper = document.createElement("div");
            wrapper.className = "page";
            fold.appendChild(wrapper);

            function renderGraphicalPage(viewport, page) {
                var canvas = document.createElement("canvas"),
                    context = canvas.getContext("2d");
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                canvas.style.backgroundColor = "#fff";
                wrapper.appendChild(canvas);

                canvas.setAttribute("data-page", i);

                page.render({
                    canvasContext: context,
                    viewport: viewport
                });

                is_text = false;
            }

            function renderTextPage(viewport, page) {
                console.log("Getting text for page...");
                page.getTextContent().then(function(text) {
                    console.log("Text: " + text)
                    var cattext = "";
                    for(var i = 0; i < text.bidiTexts.length; i++) {
                        var s = text.bidiTexts[i].str;
                        if(s == " ")
                            s = "<br>";
                        cattext += s;
                    }

                    var textbox = document.createElement("div");
                    textbox.className = "textwrap";
                    textbox.innerHTML = cattext;
                    wrapper.appendChild(textbox);
                });
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
        })(fold, i);
    }

    callback.go();

});
