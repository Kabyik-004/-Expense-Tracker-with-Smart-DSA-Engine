import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  return (
    <Router>
      <Routes>
        {/* Routes will be added here during feature development */}
        <Route path="/" element={<div>Expense Tracker</div>} />
      </Routes>
    </Router>
  );
}

export default App;
