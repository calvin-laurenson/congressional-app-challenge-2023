import { Card } from "@radix-ui/themes"
import { useState } from "react"
import { z } from "zod"

const attendanceStatus = z.enum(["absent", "tardy", "present"])

export type AttendanceStatus = z.infer<typeof attendanceStatus>

export const classAttendance = z.record(z.string(), attendanceStatus)

export type ClassAttendance = z.infer<typeof classAttendance>

const COLORS: Record<AttendanceStatus, string> = {
    present: "#3ADA34",
    absent: "#878787",
    tardy: "#FFA000"
}

export default function Attendance({ attendance }: { attendance: ClassAttendance }) {



    return (
        <div className="m-4">
            <div className="flex justify-center m-2 text-xl">
                <b>Attendance</b>
            </div>
        <div className="grid grid-cols-2 gap-4">
            {Object.keys(attendance).map(k => (
                <Card key={k}>
                    <div className="flex flex-row items-center justify-between">

                        <div className="rounded-full w-5 h-5" style={{ backgroundColor: COLORS[attendance[k]] }}>
                        </div>
                        <div>
                        {k}
                        </div>
                    </div>
                </Card>
            ))}
        </div>
        </div>
    )
}