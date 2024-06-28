import React from 'react';
import Grid from '@/components/Grid'
import './helper.js'





export default function SetAvailability() {

        return (
        <>
                <h1 id = "title"></h1>
                <h2 id = "dateRange"></h2>

                <table id="table"></table>
                
                <Grid />

                <button onClick={resetHours}>Reset</button>
                <button onClick={parseAvailability}>Submit</button>
                <script type="text/javascript" src="./main.js"></script>
        </>
        )
      
}