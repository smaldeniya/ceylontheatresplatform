var seatList = {};
var seatCount = 0;
var halfCount = 0;

jQuery(document).ready(function () {
    jQuery('td').each(function () {
        var innerCellHtml = jQuery(this).html();
        if (innerCellHtml !== "" && innerCellHtml.indexOf("&nbsp;") == -1) {

            if (reservedList.indexOf(',' + innerCellHtml + ',') == -1) {
                jQuery(this).click(function () {
                    if (jQuery(this).hasClass("selectedSeat")) {

                        jQuery(this).css("background-image", "url(../images/blankSeat.png)");
                        jQuery(this).removeClass("selectedSeat");
                        delete seatList[innerCellHtml];
                        seatCount--;

                    } else {
                        jQuery(this).css("background-image", "url(../images/selected.png)");

                        jQuery(this).addClass("selectedSeat");
                        seatList[innerCellHtml] = innerCellHtml;
                        seatCount++;
                    }
                    if (view == 'public') {
                        jQuery("#odc_half").attr("max", seatCount);
                        if (jQuery("#odc_half").val() > seatCount) {
                            jQuery("#odc_half").val(seatCount);
                        }

                    }
                    changeval();
                });
            } else {
                jQuery(this).css("background-image", "url(../images/reserved.png)");
                jQuery(this).addClass("reservedSeat");


            }
        } else {
            jQuery(this).css("background-image", "none");
        }
    });

});
function formSubmit() {
    var seatListString = "";
    var iterateSeatList = 1;
    jQuery.each(seatList, function (index, value) {
        seatListString += value + ",";
    });

    var formData = {};
    formData['seatListString'] = seatListString.substring(0, (seatListString.length - 1));

    //jQuery("#form").append('<input type="hidden" name="seatListString" value="' + seatListString.substring(0, (seatListString.length - 1)) + '">');

    formData['box_full'] = 0;
    formData['balcony_full'] = 0;
    formData['balcony_half'] = 0;
    formData['balcony_service'] = 0;
    formData['balcony_complimentary'] = 0;
    formData['odc_full'] = 0;
    formData['odc_half'] = 0;
    formData['odc_service'] = 0;
    formData['odc_complimentary'] = 0;
    formData['firstclass_full'] = 0;
    formData['firstclass_half'] = 0;
    formData['firstclass_service'] = 0;
    formData['firstclass_complimentary'] = 0;

    switch (view) {
        case "public":
            formData['odc_half'] = halfCount; // jQuery("#inp_odc_half").attr('value', halfCount);
            formData['odc_full'] = (seatCount - halfCount); //jQuery("#inp_odc_full").attr('value', (seatCount - halfCount));
            break;
        case "service":
            formData['odc_service'] = seatCount; //jQuery("#inp_odc_service").attr('value', seatCount);
            break;
        case "complimentary":
            formData['odc_complimentary'] = seatCount; //jQuery("#inp_odc_complimentary").attr('value', seatCount);
    }
    //jQuery("#form").submit();
    formData['show']= jQuery("[name=show]").val();
    formData['cinema_id']= jQuery("[name=cinema_id]").val()

    jQuery.ajaxSetup({
        beforeSend:function(){
            // show image here
            $("#busyIcon").show();
            $("#makeReservationTop").hide();
            $("#makeReservationBottom").hide();
        },
        complete:function(){
            // hide image here
            $("#makeReservationTop").show(10000);
            $("#makeReservationBottom").show(10000);
            $("#busyIcon").hide(10000);
        }
    });


    jQuery.ajax({
        url : "/seatplan",
        type: "POST",
        data : formData,
        success: function(data, textStatus, jqXHR)
        {
            if(data == "true") {
                window.location.href = "/cashier";
            } else {
                alert("Ticket booking failed !!! ");
            }
        },
        error: function (jqXHR, textStatus, errorThrown)
        {
            alert("Ticket booking failed due to system error !!! ");
        }
    });
}

function changeval() {
    jQuery("#totalCount").html(seatCount);
    if (view == "public") {
        halfCount = jQuery("#odc_half").val();

        jQuery("#halfCount").html(halfCount);
        jQuery("#fullCount").html((seatCount - halfCount));
    }
}