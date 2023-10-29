import { Button, Switch } from "@radix-ui/themes";
import { useCallback, useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import { useInterval } from "usehooks-ts"
import axios from "axios"
function dataURLtoFile(dataurl: string, filename: string) {
    var arr = dataurl.split(','),
        mime = arr[0]!!.match(/:(.*?);/)!![1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);

    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
}

export default function Camera({onFrame, isAttendanceing, setIsAttendanceing}: {onFrame: () => void, isAttendanceing: number | null, setIsAttendanceing: (v: number | null) => void}) {
    const webcamRef = useRef<Webcam & HTMLVideoElement>(null);
    const capture = useCallback(
        () => {
            const imageSrc = webcamRef.current?.getScreenshot();
            return imageSrc
        },
        [webcamRef]
    );
    const [isCameraing, setIsCameraing] = useState(false);
    const [isTardying, setIsTardying] = useState(false);

    const [timeoutID, setTimeoutID] = useState<number | null>(null)
    async function startCapturing() {
        if (isAttendanceing === null) {
            return
        }
        console.time("capture")
        const imageSrc = capture()
        console.timeEnd("capture")

        console.time("image-convert")
        const imageFile = dataURLtoFile(imageSrc!!, "image.png")
        console.timeEnd("image-convert")

        const formData = new FormData();
        formData.append("image_file", imageFile);

        console.time("fetch")
        // Send multipart/form-data request
        const resp = await axios.post("http://localhost:8000/add_image", formData, {params: {time: Date.now(), tardy: isTardying}})
        console.timeEnd("fetch")

        if (resp.status === 200 && "error" in resp.data && resp.data.error === null) {
            console.log("Good upload")
            onFrame()
        } else {
            console.log("Bad upload", resp.data)
        }
        setTimeoutID(window.setTimeout(startCapturing, 500))
    }

    async function onAttendanceSwitch(v: boolean) {
        if (isAttendanceing === null && v) {
            setIsAttendanceing(Date.now())
            startCapturing()
        } else{
            setIsAttendanceing(null)
        }
    }

    return (
        <div className="flex flex-row justify-center">
            <div className="p-2">
                <Webcam ref={webcamRef} audio={false} videoConstraints={{ facingMode: "user" }} onUserMedia={() => setIsCameraing(true)} />
                {isCameraing ? (
                    <div className="flex gap-4">
                        <div className="flex flex-col justify-center items-center">
                            <span>Record Attendance   </span>
                            <Switch checked={isAttendanceing !== null} onCheckedChange={onAttendanceSwitch} />
                        </div>
                        {isAttendanceing ? (
                            <div className="flex flex-col justify-center items-center">
                                <span>Mark Tardy</span>
                                <Switch checked={isTardying} onCheckedChange={setIsTardying} />
                            </div>
                        ) : (<div></div>)}
                    </div>
                ) : (<div>Bad</div>)}
            </div>
        </div>
    )
}