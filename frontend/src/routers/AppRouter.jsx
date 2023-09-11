import { BrowserRouter, Switch, Route, Redirect } from "react-router-dom";
import Login from "../features/Login";

// Utils
import { StyledContainer } from "../app/StyledContainer";
import ModelManager from "../features/ModelManager";
import Deployments from "../features/Deployments/Deployments";
import AdminSettings from "../features/AdminSettings";

export const AppRouter = () => {
  const isLoggedIn = localStorage.getItem("jwt");
  const role = localStorage.getItem("role");

  return (
    <BrowserRouter>
      <Switch>
        <Route exact path="/login" component={Login} />

        {isLoggedIn && (
          <StyledContainer>
            <Route exact path="/deployments" component={Deployments} />
            <Route exact path="/deployments/:id" component={ModelManager} />
            <Route
              exact
              path="/deployments/:id/overview"
              component={ModelManager}
            />
            {role && <Route exact path="/settings" component={AdminSettings} />}
            <Route
              exact
              path="/"
              render={() => <Redirect to="/deployments" />}
            />
          </StyledContainer>
        )}

        {!isLoggedIn && <Redirect to="/login" />}
      </Switch>
    </BrowserRouter>
  );
};
