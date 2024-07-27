import tensorflow as tf
print(tf.__version__)
print("Num GPUs Available: ", tf.config.experimental.list_physical_devices('GPU'))

# @app.route('/diemdanh2')
#     def diemdanh2():
#         db_all = Student.query.all()  # Lấy tất cả sinh viên để hiển thị
#         socketio.start_background_task(target=gen)
#         return render_template("diemdanh.html", students=db_all)

#     def gen():    
#         cap = cv2.VideoCapture(0)              
#         while True:
            
#             success, frame = cap.read()
#             if not success:
#                 break
#             else:           
#                 frame = cv2.flip(frame, 1)               
#                 frame = imutils.resize(frame, width=600)

#                 best_name, best_class_probabilities, frame, bbb = recognition.frame_recognition(frame)
#                 socketio.emit('update_results', {'name': best_name, 'accuracy': best_class_probabilities,'x1':bbb[0],'y1':bbb[1],'x2':bbb[2],'y2':bbb[3]})
#                 ret, buffer = cv2.imencode('.jpg', frame)
#                 frame = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#             time.sleep(.1)

    # @app.route('/video_feed')
    # def video_feed():    
    #     return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')
