var seatList={};
var seatCount=0;
var halfCount=0;

jQuery(document).ready(function(){
  jQuery('td').each(function(){
    var innerCellHtml=jQuery(this).html();
    if(innerCellHtml!=="" && innerCellHtml.indexOf("&nbsp;")==-1){

      if(reservedList.indexOf(','+innerCellHtml+',') ==-1){
	jQuery(this).click(function() {
	  if(jQuery(this).hasClass("selectedSeat")){
	    
	    jQuery(this).css("background-image","url(../images/blankSeat.png)");
	    jQuery(this).removeClass("selectedSeat");
	    delete seatList[innerCellHtml];
	    seatCount--;
	    
	  }else{
	    jQuery(this).css("background-image","url(../images/selected.png)");
	    
	    jQuery(this).addClass("selectedSeat");
	    seatList[innerCellHtml]=innerCellHtml;
	    seatCount++;
	  }
	  if(view=='public'){
	    jQuery("#odc_half").attr("max",seatCount);
	    if(jQuery("#odc_half").val()>seatCount){
	      jQuery("#odc_half").val(seatCount);    
	    }
	    
	  }
	  changeval();
	});  
      }else{
	jQuery(this).css("background-image","url(../images/reserved.png)");
	jQuery(this).addClass("reservedSeat");
	
	
      }
    }else{
      jQuery(this).css("background-image","none");
    }
  });

});
function formSubmit(){
  var seatListString="";
    var iterateSeatList=1;
  jQuery.each(seatList, function(index, value) {
      seatListString+=value+",";  
  });

  jQuery("#form").append('<input type="hidden" name="seatListString" value="'+seatListString.substring(0,(seatListString.length-1))+'">');
  switch(view){
    case "public":
      jQuery("#inp_odc_half").attr('value',halfCount);
      jQuery("#inp_odc_full").attr('value',(seatCount-halfCount));
      break;
    case "service":
      jQuery("#inp_odc_service").attr('value',seatCount);
      break;
    case "complimentary":
      jQuery("#inp_odc_complimentary").attr('value',seatCount);
  }
  jQuery("#form").submit();
  return false;
}
function changeval(){
      jQuery("#totalCount").html(seatCount);
  if(view=="public"){
    halfCount=jQuery("#odc_half").val();
    
    jQuery("#halfCount").html(halfCount);
    jQuery("#fullCount").html((seatCount-halfCount));
  }
}