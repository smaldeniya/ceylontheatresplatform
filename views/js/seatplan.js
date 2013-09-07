var seatList={};
var seatCount=0;
var halfCount=0;
if (typeof plan == 'undefined'){
  var plan='odc';//default = public
}
jQuery(document).ready(function(){
  jQuery('td').each(function(){
    var innerCellHtml=jQuery(this).html();
    if(innerCellHtml!=="" && innerCellHtml.indexOf("&nbsp;")==-1){

      if(reservedList.indexOf(','+innerCellHtml+',') ==-1){
	jQuery(this).click(function() {
	  if(jQuery(this).hasClass("selectedSeat")){
	    
	    jQuery(this).css("background-image","url(../images/u5_original.png)");
	    jQuery(this).removeClass("selectedSeat");
	    delete seatList[innerCellHtml];
	    seatCount--;
	    
	  }else{
	    jQuery(this).css("background-image","url(../images/u3_original.png)");
	    
	    jQuery(this).addClass("selectedSeat");
	    seatList[innerCellHtml]=innerCellHtml;
	    seatCount++;
	  }
	  if(view=='public' && (plan=='odc' || plan=='balcony')){
	    jQuery("#odc_half").attr("max",seatCount);
	    if(jQuery("#odc_half").val()>seatCount){
	      jQuery("#odc_half").val(seatCount);    
	    }
	    
	  }
	  changeval();
	});  
      }else{
	jQuery(this).css("background-image","url(../images/u3_original.png)");
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
  if(plan!='box'){
    switch(view){
      case "public":
	alert(plan);
	jQuery("#inp_"+plan+"_half").attr('value',halfCount);
	jQuery("#inp_"+plan+"_full").attr('value',(seatCount-halfCount));
	break;
      case "service":
	jQuery("#inp_"+plan+"_service").attr('value',seatCount);
	break;
      case "complimentary":
	jQuery("#inp_"+plan+"_complimentary").attr('value',seatCount);
    }
  }else{
      jQuery("#inp_"+plan+"_full").attr('value',seatCount);
  
  }
  jQuery("#form").submit();
  return false;
}
function changeval(){
      jQuery("#totalCount").html(seatCount);
  if(view=="public" && (plan=='odc' || plan=='balcony')){
    halfCount=jQuery("#odc_half").val();
    
    jQuery("#halfCount").html(halfCount);
    jQuery("#fullCount").html((seatCount-halfCount));
  }
}