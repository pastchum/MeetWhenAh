import SummaryCard from '@/components/datepicker/Summary/SummaryCard'
import NextButton from '@/components/datepicker/NextButton'
import PreviousButton from '@/components/datepicker/PreviousButton'

export default function Summary({ data, prevComponent, nextComponent}) {
    
    return (
        <div className="relative w-[80vw] sm:w-[60vw]">
            <SummaryCard data={data} />
            <div className="absolute left-0">
                <PreviousButton onClick={prevComponent} />
            </div>
            <div className="absolute right-0">
                <NextButton onClick={nextComponent} newData={data}/>
            </div>
        </div>
    )
}