import { Link } from "react-router-dom"
const Navbar =()=>{
      return (
            <div>
                  <Link to="/">Home</Link>
                  <Link to="/Date Range">Date Range</Link>
                  <Link to="/Event Message">Event Message</Link>
            </div>
      )
}
export default Navbar;