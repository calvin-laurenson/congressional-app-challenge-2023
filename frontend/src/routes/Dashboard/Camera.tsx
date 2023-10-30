import { Button, Switch } from "@radix-ui/themes";
import { useCallback, useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import { useInterval } from "usehooks-ts"
import axios from "axios"

// export default function Camera({onFrame, isAttendanceing, setIsAttendanceing}: {onFrame: () => void, isAttendanceing: number | null, setIsAttendanceing: (v: number | null) => void}) {
//     const webcamRef = useRef<Webcam & HTMLVideoElement>(null);
//     const capture = useCallback(
//         () => {
//             const imageSrc = webcamRef.current?.getScreenshot();
//             return imageSrc
//         },
//         [webcamRef]
//     );
//     const [isCameraing, setIsCameraing] = useState(false);
//     const [isTardying, setIsTardying] = useState(false);

//     const [timeoutID, setTimeoutID] = useState<number | null>(null)
//     async function startCapturing() {
//         if (isAttendanceing === null) {
//             console.log("Stopping capturing. Attendanceing is ", isAttendanceing);
            
//             return
//         }
//         console.time("capture")
//         const imageSrc = capture()
//         console.timeEnd("capture")

//         console.time("image-convert")
//         const imageFile = dataURLtoFile(imageSrc!!, "image.png")
//         console.timeEnd("image-convert")

//         const formData = new FormData();
//         formData.append("image_file", imageFile);

//         console.time("fetch")
//         // Send multipart/form-data request
//         const resp = await axios.post("http://localhost:8000/add_image", formData, {params: {time: Date.now(), tardy: isTardying}})
//         console.timeEnd("fetch")

//         if (resp.status === 200 && "error" in resp.data && resp.data.error === null) {
//             console.log("Good upload")
//             onFrame()
//         } else {
//             console.log("Bad upload", resp.data)
//         }
//         setTimeoutID(window.setTimeout(startCapturing, 500))
//     }

//     async function onAttendanceSwitch(v: boolean) {
//         if (isAttendanceing === null && v) {
//             setIsAttendanceing(Date.now())
//             await startCapturing()
//         } else{
//             setIsAttendanceing(null)
//         }
//     }

//     return (
       
//     )
// }