$(document).ready(function(){
	$('#btnSignUp').click(function(){
		
		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
                var result = JSON.parse(response);
                if(result['status'] === 'Success'){
                    window.alert('Successful');
                    window.location = "/showsignin";
                } else console.log(result['status']);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
