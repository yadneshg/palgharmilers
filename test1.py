import os

from werkzeug.utils import secure_filename
file='x.jpg'
names=['1.jpg','2.jpg','3.jpg','4.jpg','5.jpg','6.jpg']
for name in names:
    for i in range(100):
        n = f"{i}.jpg"
        if n == name:
            continue
        else:
            dd=n
            break

if file != name:
    #filename = secure_filename(file.filename)
    #file.save(os.path.relpath(f"static/uploads/{filename}"))
    ff=f"{file}"
    print(dd)
    print(ff)
    names.append(dd)
    print(names)
    #os.rename(ff, dd)


