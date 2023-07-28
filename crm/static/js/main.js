function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("main-content").style.marginLeft = "250px";
    document.getElementById("openbtn").style.display = "none";
}

function closeNav() {
    document.getElementById("mySidebar").style.width = "60px";
    document.getElementById("main-content").style.marginLeft = "60px";
    document.getElementById("openbtn").style.display = "block";
}
$("#yapilacaklarBtn").click(function () {
    $("#yapilacaklarPanel").toggle();
});

$("#addYapilacakBtn").click(function () {
    var yapilacak = $("#yapilacakInput").val();
    var detay = $("#detayInput").val();
    $.post("{% url 'musteri:add_yapilacak' %}", { yapilacak: yapilacak, detay: detay }, function (data) {
        if (data.success) {
            var yapilacakItem = "<li>" + yapilacak + ": " + detay + '<button class="tamamlandiBtn">✔️</button>' + "</li>";
            $("#yapilacaklarList").prepend(yapilacakItem);
            $("#yapilacakInput").val("");
            $("#detayInput").val("");
        }
    });
});

$("#yapilacaklarList").on("click", ".tamamlandiBtn", function () {
    var id = $(this).parent().attr("id");
    var btn = $(this);
    $.post(completeYapilacakUrlBase + id, function (data) {
        if (data.success) {
            btn.parent().css("text-decoration", "line-through");
            btn.parent().css("color", "#ccc");
        }
    });
});



