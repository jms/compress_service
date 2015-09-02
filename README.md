Compress service

notes:

process:  

	rqworker default

monitoring queue and worker
	
	rqinfo --interval 5
	
	rq-dashboard 


test with httpie:
	
	http POST http://localhost:8000/compress id=1 file_list:='["abc.jpb", "xyz.png"]' bucket:abc


