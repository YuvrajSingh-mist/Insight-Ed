"use client"
import React from "react";
import { useEffect, useState } from "react";
import getAllLectures from "@/actions/TeacherProfile";
import Subject from "@/app/components/SubjectComponent";
import Loader from "@/app/components/Loader";
import { useRouter } from "next/navigation";
interface LectureData {
    id: string;
    title: string;
    link: string;
}
export default function AllLectures({params}:any){
    //console.log(params.lecture);
    const router = useRouter();
    const [lectures, setLectures] = useState<LectureData[]>([]);
    const [loading, setLoading] = useState(false);
    useEffect(()=>{
        async function allLectures(){
            setLoading(true);
            const lectures = await getAllLectures(params.lecture); //subject id
            setLectures(lectures);
            setLoading(false);
        }
        allLectures();
    },[params.lecture])

    return (
        <div>
          {loading ? (
            <Loader/>
          ) : (
            <div>
              <h1 className="text-center text-3xl font-bold mb-6">All Lectures</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {lectures.map((lecture) => (
                  <div key={lecture.id}>
                  <Subject
                    key={lecture.id}
                    title={lecture.title}
                    description={lecture.link}
                    subjectid={lecture.id}
                    isStudent={true}
                    yourCourses={false}
                  />
                  <button className="bg-purple-500 hover:bg-purple-700 text-black font-bold py-2 px-4 rounded transition duration-300 ease-in-out transform hover:-translate-y-1 hover:scale-110 mt-2" onClick={()=>{
                    router.push(`/profile/teacher/alllecture/addlink/${lecture.id}`)
                  }}>Add uploaded link</button>
                  </div>
                ))}
                
              </div>
            </div>
          )}
        </div>
      );
}



{/* <div className="space-y-4">
    {lectures.map((lecture) => (
        <div key={lecture.id} className="p-4 max-w-sm mx-auto bg-white rounded-xl shadow-md flex items-center space-x-4">
            <div className="flex-shrink-0">
                <img src="/love-icon.png" alt="love for learning" className="h-12 w-12 object-cover rounded-full" />
            </div>
            <div>
                <div className="text-xl font-medium text-black">Title: {lecture.title}</div>
                <p className="text-gray-500">Link: {lecture.link}</p>
                {/* Add any additional information or buttons here */}
//             </div>
//         </div>
//     ))}
// </div> */}