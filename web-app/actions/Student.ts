"use server"

import client from "@/db"
export async function StudentSignup(username:string, firstname:string, lastname:string, password:string, phoneno:string, address:string, email:string){
    try {
        const student = await client.student.create({
            data:{
                username,
                email,
                firstname,
                lastname,
                phoneno,
                address,
                password
            }
        })
        if(student){
            console.log('Student created successfully with id: '+student.id);
            return student.id;
        }
    } catch (error) {
        console.log(error);
        return -1;
    }
}

export async function StudentSignin(email:string, password:string) {
    try {
        const student = await client.student.findUnique({
            where:{
                email,
                password
            }
        })
        if(student){
            console.log('student is successfully signed in having the id '+student.id);
            return student.id;
        }
    } catch (error) {
        console.log(error);
        return -1;
    }
}

export async function getStudentDetails(id:string) {
    try {
        const student = await client.student.findUnique({
            where:{
                id:id
            }
        });
        if(student){
            const username = student.username;
            const email = student.email;
            const id = student.id;

            return {username, email, id};
        }
    } catch (error) {
        console.log(error);
    }
}

export async function RegisterCourse(subjectId:string, studentemail:string) {
    console.log('hit');
    
    try {
        const subject = await client.subject.findUnique({
            where:{
                id:subjectId
            }, include:{
                teacher:true
            }
        })
        //console.log(subject?.teacher.id);
        if(subject){
            const student = await client.student.findUnique({
                where:{
                    email:studentemail
                }
            })
            //console.log(student);
            
            if(student){
                const studentid = student.id;
                const isRegistered = await client.studentsubject.findMany({
                    where:{
                        subjectid:subjectId,
                        studentid:studentid
                    }
                })
                console.log('Logging is Registered');
                
                console.log(isRegistered.length);
                
                if(isRegistered.length != 0){
                    return "";
                }else{
                    const register = await client.studentsubject.create({
                        data:{
                            studentid:studentid,
                            subjectid:subjectId
                        }
                    })
                    const teacherStudent = await client.studentteacher.create({
                        data:{
                            studentid:student.id,
                            teacherid:subject.teacher.id
                        }
                    })
                    if(register && teacherStudent){
                        console.log('Registration id ' + register.id);
        
                        return student.id;
                        
                    }
                }
            }
        }
        
    } catch (error) {
        console.log(error);
        return -1;
    }
}

export async function YourCourses(studentid:string) {
    const studentSubject = await client.studentsubject.findMany({
        where:{
            studentid:studentid
        },
        select:{
            subject:true
        }
    });

    const subjects = studentSubject.map((e)=> e.subject);

    return subjects;
}



export async function getScheduledLectures(studentId: string) {
    const studentTeachers = await client.studentteacher.findMany({
      where: {
        studentid: studentId,
      },
      select: {
        teacherid: true,
      },
    });
  
    const teacherIds = studentTeachers.map((st) => st.teacherid);
  
    const today = new Date().toLocaleDateString('en-GB') // Get today's date
  
    const scheduledLectures = await client.lecture.findMany({
      where: {
        teacherid: {
          in: teacherIds,
        },
        date: today,
      },
    });

    const teachers = await client.teacher.findMany({
        where: {
            id: {
                in: teacherIds,
            },
        },
        select: {
            firstname: true,
            lastname: true,
            id:true
        },
    });

    const scheduledLecturesWithTeachers = scheduledLectures.map((lecture) => {
        const teacher = teachers.find((t) => t.id === lecture.teacherid);
        const teacherInfo = teacher
            ? { firstname: teacher.firstname, lastname: teacher.lastname }
            : { firstname: 'Unknown', lastname: 'Teacher' };
        return {
            ...lecture,
            teacher: teacherInfo
        };
    });

    //console.log(scheduledLectures);
    
  
    return scheduledLecturesWithTeachers;
  }

  export async function getVideoLinkFromLectureId(lectureid:string){
    try {
      const lecture = await client.lecture.findUnique({
        where:{
          id:lectureid
        }
      })
      if(lecture){
        console.log("Lecture found:", lecture);
        return lecture.link
      } else {
        console.log("Lecture not found.");
        return ""
      }
    } catch (error) {
      console.log("Error finding lecture:", error);
      return ""
    }
  }