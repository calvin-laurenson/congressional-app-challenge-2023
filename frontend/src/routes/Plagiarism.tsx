import { Button, TextArea } from "@radix-ui/themes";
import axios from "axios";
import { useState } from "react";

export default function Plagiarism() {
    const [text1, setText1] = useState("")
    const [text2, setText2] = useState("")

    const [similarity, setSimilarity] = useState<string | null>(null)

    function similarityCheck() {
        axios.get("http://localhost:8000/get_plagiarized", { params: { writing1: text1, writing2: text2 } }).then((resp) => {
            // console.log(resp);

            // console.log("Set similarity", resp.data.similarity);
            const similarity = resp.data.similarity
            setSimilarity((similarity * 100).toFixed(2).toString())
        })
    }

    return (
        <div className="flex flex-col" style={{ height: "calc(100vh - 2.5rem)" }}>
            <div className="mt-2">
                Text Similarity
            </div>
            <div className="flex flex-row h-full">
                <div className="flex-grow m-4 flex flex-col">
                    <div>
                        Text 1
                    </div>
                    <TextArea value={text1} onChange={(e) => setText1(e.target.value)} className="flex-grow w-full" />
                </div>
                <div className="flex-grow m-4 flex flex-col">
                    <div>
                        Text 2
                    </div>
                    <TextArea value={text2} onChange={(e) => setText2(e.target.value)} className="flex-grow w-full" />
                </div>
            </div>
            <div className="mb-2 flex flex-row justify-center gap-8">
                <div>
                    <Button onClick={() => similarityCheck()}>Check</Button>
                </div>
                <div>
                    {similarity ?? "--.--"}%
                </div>
            </div>
        </div>
    )
}
