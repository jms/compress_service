Compress service

notes:

process:  

	rqworker default

monitoring queue and worker
	
	rqinfo --interval 5
	
	rq-dashboard 


test with httpie:
	
	http POST http://localhost:8000/compress id=1 file_list:='["abc.jpb", "xyz.png"]' bucket:abc


test plain without nginx

    cd compress_service 
    sudo authbind  gunicorn zipit:app -b 0.0.0.0:80 --log-level debug --user 1000 

    # or 

    gunicorn zipit:app -b 0.0.0.0:8000 --log-level debug --user 1000 
    
    
test data 

    http POST http://server:8000/compress < test_data.json

