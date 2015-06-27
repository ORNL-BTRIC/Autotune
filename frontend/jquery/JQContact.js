
$(document).ready(function() {
	$("#mailto").submit(function() {
		//validate
		$(".reminder").remove();
		if(!valid()) {
			//add <span class="important">*</span> to inputs that the user failed to fill
			//add message at bottom "Not all fields have been completed"
		
			$(":input[required=required]").each(function() {
				if($(this).val() == "") {
					$(this).before('<span class="important reminder">*</span>');
					console.log("Go!");
				}
			});
			$("form").append('<div class="important reminder">Not all fields have been completed</div>');
		}
		else {
			//after validation, show modal dialog with results from php
			var to = $(":input[name=to]").val();
			var from = $(":input[name=from]").val();
			var subject = $(":input[name=subject]").val();
			var body = $(":input[name=body]").val();
			var fName = $(":input[name=fName]").val();
			var lName = $(":input[name=lName]").val();
			console.log(to + " " + from + " " + subject + " " + body + " " + fName + " " + lName);
			$.post('contactRequest.php',
					{
					to:to,
					from:from,
					subject:subject,
					body:body,
					fName:fName,
					lName:lName
					},
					function(data) {
						$("#ajaxOutput").text(data);
					}
			);
			$("#ajaxOutput").show();
			$("#dialog-modal").dialog("open");
		}
		
		return false;
	});
	
	//modal dialog
	$("#dialog-modal").dialog({
		autoOpen: false,
		modal: true,
		buttons: {
			Ok: function() {
				$(this).dialog("close");
				window.location = "http://inspired.jsu.edu/autotune/home.html";
			}
		}
    });

});

function valid() {
	var valid = true;
	$(":input[required=required]").each(function() {
		if($(this).val() == "") {
			valid = false;
		}
	});
	console.log(valid);
	return valid;
}
