import { Card } from "@radix-ui/themes";
import React from "react";
import { useState } from "react"
import z from "zod"
const teamSchema = z.object({
    id: z.number(),
    team_name: z.string(),
    team_members: z.array(z.object({
        id: z.number(),
        name: z.string(),
    })),
})

type Team = z.infer<typeof teamSchema>

export default function Team({ teamID }: { teamID: number }) {
    const [isEditing, setIsEditing] = useState(false)

    return (
        <Card>

        </Card>
    )
}